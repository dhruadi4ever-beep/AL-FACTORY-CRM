package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class PaymentRow(
    val worker: String,
    val item: String,
    val bunches: String,
    val strips: String,
    val amount: String,
    val status: String,
)

@Composable
fun JobWorkerPaymentScreen() {
    val rows = remember {
        listOf(
            PaymentRow("Worker A", "Item A", "25", "250", "₹8000", "Pending"),
            PaymentRow("Worker B", "Item B", "50", "500", "₹16000", "Partially Paid"),
        )
    }

    var worker by remember { mutableStateOf("Worker A") }
    var bunches by remember { mutableStateOf("25") }
    var amount by remember { mutableStateOf("3000") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Job Worker Payment & Cycle Management", style = MaterialTheme.typography.headlineMedium)
        Text(text = "New assignments complete prior work automatically and calculate payment from item master values")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = worker, onValueChange = { worker = it }, label = { Text("Job Worker") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = bunches, onValueChange = { bunches = it }, label = { Text("Bunches") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = amount, onValueChange = { amount = it }, label = { Text("Payment") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Pending Payments", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(rows) { row ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            Text(text = row.worker, style = MaterialTheme.typography.titleSmall)
                            Text(text = "Item: ${row.item}")
                            Text(text = "Bunches: ${row.bunches}")
                        }
                        Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            Text(text = "Strips: ${row.strips}")
                            Text(text = "Amount: ${row.amount}")
                            Text(text = row.status)
                        }
                    }
                }
            }
        }
    }
}
